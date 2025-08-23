# 🎬 Video Retrieval System - KIS Challenge

## 📋 Tổng quan bài toán

Hệ thống **Keyframe-based Image Search (KIS)** cho phép tìm kiếm video thông qua mô tả văn bản. Khi người dùng nhớ mơ hồ một cảnh nào đó trong video, họ có thể mô tả bằng văn bản để tìm lại video chứa cảnh đó.

### 🎯 Mục tiêu Phase hiện tại
Xây dựng pipeline để đưa dữ liệu đã được tiền xử lý lên **Qdrant Vector Database**, bao gồm:
- CLIP features (512-dim vectors) 
- Metadata keyframes (timestamp, frame index)
- Object detection results
- Structured payload cho việc tìm kiếm

## 📊 Cấu trúc dữ liệu

### 🗂️ Dataset Overview
```
Tổng số file npy: 873 video
Tổng số vector (keyframes): 177,321 frames
Mỗi vector: 512 dimensions (CLIP ViT-B/32)
```

### 📁 Cấu trúc thư mục
```
data/
├── clip-features-32-aic25-b1/clip-features-32/
│   ├── L21_V001.npy (307, 512) float16
│   ├── L22_V001.npy (298, 512) float16
│   └── ... (873 files)
├── map-keyframes-aic25-b1/map-keyframes/
│   ├── L21_V001.csv (metadata: pts_time, frame_idx)
│   └── ... (873 files)
├── objects-aic25-b1/objects/
│   ├── L21_V001/
│   │   ├── 0001.json (detection results)
│   │   └── ... (N files tương ứng N keyframes)
│   └── ...
└── Keyframes_LXX/keyframes/
    ├── L21_V001/
    │   ├── 001.jpg
    │   ├── 002.jpg
    │   └── ... (307 images)
    └── ...
```

### 📄 Format dữ liệu chi tiết

#### CSV Metadata (map-keyframes)
```csv
n,pts_time,fps,frame_idx
1,0,30,0
2,3,30,90
3,8.7,30,261
```

#### Object Detection JSON
```json
{
  "detection_scores": ["0.79673874", "0.6866252"],
  "detection_class_names": ["/m/01jfsr", "/m/079cl"],
  "detection_class_entities": ["Lantern", "Skyscraper"],
  "detection_boxes": [["0.46860334", "0.36642352", ...]],
  "detection_class_labels": ["84", "379"]
}
```

## 🏗️ Kiến trúc Qdrant Database

### 📝 Schema thiết kế

```json
{
  "id": "L21_V001_001",
  "vector": [512 dimensions],
  "payload": {
    "video_id": "L21_V001",
    "keyframe_idx": 1,
    "keyframe_name": "001.jpg",
    "jpg_path": "Keyframes_L21/keyframes/L21_V001/001.jpg",
    "pts_time": 0.0,
    "frame_idx": 0,
    "fps": 30,
    "objects": [
      {
        "entity": "Lantern",
        "class_name": "/m/01jfsr",
        "score": 0.79673874,
        "bbox": [0.46860334, 0.36642352, 0.58123, 0.71234]
      }
    ],
    "object_labels": ["Lantern", "Skyscraper"],
    "high_confidence_objects": ["Lantern"],  // score > 0.7
    "object_count": 2,
    "batch": "L21",  // để phân loại theo batch
    "has_objects": true
  }
}
```

### 🔧 Qdrant Collection Configuration

```python
collection_config = {
    "collection_name": "video_keyframes",
    "vectors": {
        "size": 512,
        "distance": "Cosine"  # Tương thích với CLIP embeddings
    },
    "optimizers_config": {
        "default_segment_number": 16,  # Tối ưu cho ~200K vectors
        "memmap_threshold": 20000
    },
    "hnsw_config": {
        "m": 16,
        "ef_construct": 200,
        "ef": 128
    }
}
```

## 🚀 Pipeline thực hiện

### Phase 1: Data Preprocessing & Loading

#### 🔄 Step 1: Scan và validate dữ liệu
```python
def scan_dataset():
    """
    - Scan tất cả .npy files
    - Validate shape (N, 512)
    - Check tương ứng .csv và object folders
    - Generate summary report
    """
```

#### 🔄 Step 2: Batch processing từng video
```python
def process_video(video_id):
    """
    1. Load CLIP features: np.load(f"{video_id}.npy")
    2. Load metadata: pd.read_csv(f"{video_id}.csv") 
    3. Load objects: glob(f"objects/{video_id}/*.json")
    4. Combine và tạo Qdrant points
    """
```

#### 🔄 Step 3: Object detection preprocessing
```python
def preprocess_objects(detection_json):
    """
    - Convert scores to float
    - Filter by confidence threshold (>0.5)
    - Normalize bbox coordinates
    - Create object summary
    """
```

### Phase 2: Qdrant Integration

#### 📤 Upload strategy
```python
def upload_to_qdrant():
    """
    - Batch upload (1000 points/batch)
    - Progress tracking
    - Error handling & retry
    - Verify uploaded data
    """
```

#### 🎯 Indexing strategy
- **Primary index**: CLIP vector similarity (Cosine)
- **Payload filters**: 
  - `video_id` (keyword)
  - `object_labels` (keyword array)
  - `pts_time` (range filter)
  - `has_objects` (boolean)

### Phase 3: Search & Retrieval

#### 🔍 Search modes
1. **Semantic search**: Text → CLIP embedding → Vector similarity
2. **Object-based search**: Filter by object types
3. **Hybrid search**: Combine semantic + object filters
4. **Temporal search**: Tìm trong khoảng thời gian cụ thể

#### 📊 Search result format
```json
{
  "results": [
    {
      "score": 0.95,
      "video_id": "L21_V001", 
      "keyframe": "001.jpg",
      "timestamp": "00:00:00",
      "objects": ["Lantern", "Skyscraper"],
      "image_url": "/api/keyframes/L21_V001/001.jpg"
    }
  ],
  "total": 50,
  "query_time": "45ms"
}
```

## ⚡ Tối ưu hóa hiệu suất

### 🗄️ Database Optimization
- **Vector compression**: Sử dụng `float16` thay vì `float32` 
- **Disk optimization**: SSD storage cho Qdrant
- **Memory management**: Configure memory mapping cho large dataset
- **Sharding**: Chia collection theo batch nếu cần

### 🔍 Search Optimization  
- **Pre-filtering**: Filter payload trước khi vector search
- **Caching**: Cache frequent queries
- **Batch queries**: Xử lý nhiều queries cùng lúc

### 📊 Monitoring & Analytics
- Track search latency
- Monitor memory usage
- Log popular queries
- A/B test search relevance

## 🛠️ Implementation Plan

### ⏱️ Timeline
1. **Week 1**: Setup Qdrant + Data validation
2. **Week 2**: Implement preprocessing pipeline  
3. **Week 3**: Batch upload + indexing
4. **Week 4**: Search API + testing

### ✅ Deliverables
- [ ] Data preprocessing scripts
- [ ] Qdrant upload pipeline
- [ ] Search API endpoints
- [ ] Performance benchmarks
- [ ] Documentation

### 🔧 Tech Stack
- **Vector DB**: Qdrant
- **Processing**: Python + NumPy + Pandas
- **CLIP Model**: OpenAI CLIP ViT-B/32
- **API**: FastAPI (for search endpoints)
- **Monitoring**: Prometheus + Grafana

## 📈 Expected Performance

### 🎯 Search Performance
- **Latency**: < 100ms for top-10 results
- **Throughput**: > 100 queries/second
- **Accuracy**: > 85% relevance score

### 💾 Storage Requirements
- **Vectors**: ~340MB (177K × 512 × 4 bytes)
- **Payload**: ~50MB (metadata + objects)
- **Total Qdrant**: ~500MB
- **Images**: Không lưu trong Qdrant (chỉ references)

---

🔥 **Next Phase**: Web application với search interface và video playback functionality
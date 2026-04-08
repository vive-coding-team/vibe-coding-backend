# vibe-coding-backend

PDF/PPTX 파일에서 텍스트를 추출하는 Flask API.

## 실행

가상환경(venv) 사용 권장.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

## API

### `POST /extract`

`multipart/form-data`로 업로드.

- `files`: 여러 개 업로드 (권장)
- `file`: 단일 업로드

예시:

```bash
curl -X POST "http://localhost:5000/extract" \
  -F "files=@sample.pdf" \
  -F "files=@sample.pptx"
```

응답:

```json
{
  "count": 2,
  "results": [
    {"filename": "sample.pdf", "content_type": "application/pdf", "ok": true, "body": ["1페이지 텍스트", "2페이지 텍스트"], "error": null},
    {"filename": "sample.pptx", "content_type": "application/vnd.openxmlformats-officedocument.presentationml.presentation", "ok": true, "body": ["1슬라이드 텍스트", "2슬라이드 텍스트"], "error": null}
  ]
}
```

## 참고

- `.ppt`(구형 바이너리 포맷)를 업로드하면 서버에서 PDF로 자동 변환 후 텍스트를 추출합니다. (서버에 LibreOffice 설치 필요)
- 기본 업로드 제한은 50MB이며 `MAX_CONTENT_LENGTH` 환경변수로 조정할 수 있습니다.


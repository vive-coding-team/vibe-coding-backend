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

## Railway 배포

- **시작**: 저장소 루트의 `Procfile`로 `gunicorn`이 실행되며, Railway가 주입하는 **`PORT`**에 바인딩합니다.
- **환경 변수** (예시): `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, 필요 시 `MAX_CONTENT_LENGTH`, `FLASK_DEBUG=0`
- **`.ppt` 변환**: `nixpacks.toml`에서 `libreoffice`를 apt로 설치합니다. 빌드가 무겁거나 실패하면 해당 파일에서 `aptPkgs`를 조정하세요.

## API

### `POST /extraction`

`multipart/form-data`로 업로드.

- `file`: 단일 파일만 (필수)

예시:

```bash
curl -X POST "http://localhost:5000/extraction" \
  -F "file=@sample.pdf"
```

응답:

```json
{
  "count": 1,
  "results": [
    {
      "filename": "sample.pdf",
      "content_type": "application/pdf",
      "ok": true,
      "body": ["1페이지 텍스트", "2페이지 텍스트"],
      "error": null,
      "supabase": {"ok": true, "id": 1, "error": null}
    }
  ]
}
```

## 참고

- `.ppt`(구형 바이너리 포맷)를 업로드하면 서버에서 PDF로 자동 변환 후 텍스트를 추출합니다. (서버에 LibreOffice 설치 필요)
- 기본 업로드 제한은 50MB이며 `MAX_CONTENT_LENGTH` 환경변수로 조정할 수 있습니다.


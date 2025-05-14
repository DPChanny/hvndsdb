# hvndsdb

## 프로젝트 구조
project (root 폴더) # => 수정해도 ok
- backend: FastAPI 백엔드
- client: React 프론트엔드
- unity: Unity 프로젝트

## 개발 및 실행 방법

### 1. 의존성 설치

#### 백엔드
```bash
cd backend
pip install -r requirements.txt

### 추가 예정
```

#### 프론트엔드
```bash
cd client
npm install
```

### 2. 개발 서버 실행

#### 백엔드
```bash
cd backend
uvicorn app.main:app --reload
```

#### 프론트엔드
```bash
cd client
npm start
```

### 3. Docker로 전체 실행

```bash
docker-compose up --build
```

## 환경 변수
- `.env` 파일에 DB, S3 등 민감 정보를 저장 (예시: `DATABASE_URL=...`)

## GitHub 업로드 방법

1. git 초기화 및 원격 저장소 연결
```bash
git init
git remote add origin https://github.com/사용자명/레포명.git
```
2. 커밋 및 푸시
```bash
git add .
git commit -m "프로젝트 업로드"
git push -u origin main
```

---
추가 문의사항은 이슈로 남겨주세요!

# 빌드 스테이지: Node 22 (vite 8 요구사항)
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
# 카톡/페북 공유 썸네일용 OG 이미지 절대 URL (배포 도메인, 서브패스 포함)
ARG SITE_URL=
# 서브패스 배포 시 /media-stats-analysis-competition/ 처럼 앞뒤 슬래시 포함
ARG BASE_PATH=/
ENV SITE_URL=$SITE_URL BASE_PATH=$BASE_PATH
RUN npm run build

# 서빙 스테이지: 정적 파일만 nginx로 (BASE_PATH 위치에 그대로 놓아 호스트 nginx가 URI 변경 없이 프록시)
FROM nginx:alpine
ARG BASE_PATH=/
COPY --from=build /app/dist /usr/share/nginx/html${BASE_PATH}
EXPOSE 80

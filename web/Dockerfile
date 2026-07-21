# 빌드 스테이지: Node 22 (vite 8 요구사항)
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
# 카톡/페북 공유 썸네일용 OG 이미지 절대 URL (배포 도메인)
ARG SITE_URL=
ENV SITE_URL=$SITE_URL
RUN npm run build

# 서빙 스테이지: 정적 파일만 nginx로
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80

FROM node:20-alpine

WORKDIR /app

# Копируем только package.json для кэширования слоев
COPY package*.json ./
RUN npm install

# Копируем весь остальной код
COPY . .

# Открываем порт Vite
EXPOSE 5173

# Запускаем Dev-сервер. Флаг --host 0.0.0.0 обязателен для Docker
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
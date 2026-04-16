FROM node:20-alpine

WORKDIR /usr/src/app

COPY package*.json ./

RUN npm install

COPY . .

# Place the CTF flag
RUN echo "apteshr{tell_ME_are_you_0_OR_1**you have root permission}" > /flag.txt

EXPOSE 5000

CMD ["npm", "start"]

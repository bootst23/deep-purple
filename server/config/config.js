import dotenv from 'dotenv';
dotenv.config();


export const port = 8081;

//DATABASE HOSTED ON RENDER
export const DB = {
    user: process.env.DB_USER,
    host: process.env.DB_HOST,
    database: process.env.DB_NAME,
    password: process.env.DB_PASS,
    port: process.env.DB_PORT,
    url: process.env.DB_URL
};

export const authentication = {
    jwtSecret: process.env.JWT_SCRETE || 'secret'
};
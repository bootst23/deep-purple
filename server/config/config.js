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
    url: "postgresql://root:ttitSwC4qeuvtJr9guF9mwpHu3dQUtfV@dpg-ctao56aj1k6c738nu9f0-a.oregon-postgres.render.com/deep_purple_database_9ubd"
};

export const authentication = {
    jwtSecret: process.env.JWT_SCRETE || 'secret'
};
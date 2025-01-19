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
    url: "postgresql://root:tGWKO7GE4MmAGCOZ2b16OpAkiZCQF07w@dpg-cti9ga3tq21c739m9tdg-a.singapore-postgres.render.com/deep_purple_database_101f"
};

export const authentication = {
    jwtSecret: process.env.JWT_SCRETE || 'secret'
};
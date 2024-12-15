import fs from 'fs';
import path from 'path';
import { Sequelize } from 'sequelize';
import { fileURLToPath, pathToFileURL } from 'url'; 
import { DB } from '../config/config.js';

const db = {};

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);


//Connect to Postgre Database Hosted on Render
const sequelize = new Sequelize(DB.url,{
    dialect: "postgres",
    protocol: "postgres",
    dialectOptions: {
    ssl: {
        require: true,
        rejectUnauthorized: false,
    },
    },
    logging: false,
});

async function loadModels() {
    const files = fs.readdirSync(__dirname);

    for (const file of files) {
        if (file !== 'index.js') {
            // Convert the path to a valid file:// URL
            const filePath = pathToFileURL(path.join(__dirname, file)).href;
            const modelModule = await import(filePath); // Dynamic import using file URL
            const model = modelModule.default(sequelize, Sequelize.DataTypes); // Initialize model
            db[model.name] = model; // Add model to db object
        }
    }

    db.sequelize = sequelize; 
    db.Sequelize = Sequelize; 
}

await loadModels();
export { db };

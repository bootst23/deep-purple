import express from 'express'
import bodyParser from 'body-parser'
import cors from 'cors'
import morgan from 'morgan'
import { db } from './models/index.js';
import {port, DB} from './config/config.js';
import setupRoutes from './routes.js';
import dotenv from 'dotenv';
dotenv.config();

const app = express()
const { sequelize } = db;
app.use(morgan('combined'))
app.use(bodyParser.json())
app.use(cors())
setupRoutes(app);


sequelize.sync().then(() =>{
    app.listen(8081 || `https://deep-purple-server-gc60.onrender.com`)
    console.log(`Server Started on ${port}`)
    console.log(DB.password)
})




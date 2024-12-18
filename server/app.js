import express from 'express'
import bodyParser from 'body-parser'
import cors from 'cors'
import morgan from 'morgan'
import { db } from './models/index.js';
import {port, DB} from './config/config.js';
import setupRoutes from './routes.js';

const app = express()
const { sequelize } = db;
app.use(morgan('combined'))
app.use(bodyParser.json())
app.use(cors())
setupRoutes(app);


sequelize.sync().then(() =>{
    app.listen(process.env.PORT || 8081)
    console.log(`Server Started on ${port}`)
    console.log(DB.password)
})




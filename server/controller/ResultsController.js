/* eslint-disable @typescript-eslint/no-unused-vars */
import { db } from '../models/index.js';  // Import the db object that contains all models

const { Results } = db;  // Destructure to get the Results model

export async function post(req, res) {
    try {
        const result = await Results.create(req.body)
        res.send(result)
    } catch (err) {
        res.status(500).send({
            error: 'Error Occured Creating Results.'
        });
    }
}

export async function index(req, res) {
    try {
        const result = await Results.findAll({
            limit: 10                     //Return all results in the database
        })
        res.send(result)
    } catch (err) {
        res.status(500).send({
            error: 'Error Occured Getting Results.'
        });
    }
}

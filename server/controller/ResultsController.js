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
            order: [['createdAt', 'DESC']]  // Most recent timestamps first
        })
        res.send(result)
    } catch (err) {
        res.status(500).send({
            error: 'Error Occurred Getting Results.'
        });
    }
}

export async function show(req, res) {
    try {
        const result = await Results.findByPk(req.params.resultId);  //Fond Specific Result
        if (!result) {
            return res.status(404).send({
                error: 'Result not found.'
            });
        }
        res.send(result);
    } catch (err) {
        console.error('Error in /results/:resultId:', err); // Log error details
        res.status(500).send({
            error: 'Error Occurred Getting Results.'
        });
    }
}

export async function destroy(req, res) {
    try {
      const resultId = parseInt(req.params.resultId);
      if (isNaN(resultId)) {
        return res.status(400).send({ error: 'Invalid result ID.' });
      }
  
      const result = await Results.findByPk(resultId);
      if (!result) {
        return res.status(404).send({ error: 'Result not found.' });
      }
  
      await result.destroy(); // Deletes the result
      res.send({ message: 'Result deleted successfully.' });
    } catch (err) {
      console.error(`Error deleting result with ID ${req.params.resultId}:`, err);
      res.status(500).send({ error: `Error Occurred Deleting Result: ${err.message}` });
    }
  }
  


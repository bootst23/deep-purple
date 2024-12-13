/* eslint-disable @typescript-eslint/no-unused-vars */
import { db } from '../models/index.js';  // Import the db object that contains all models

const { User } = db;  // Destructure to get the User model
import jwt from 'jsonwebtoken'
import {authentication} from '../config/config.js'

function jwtSignUser(user){
    const ONE_WEEK = 60 * 60 * 24 * 7
    return jwt.sign(user, authentication.jwtSecret, {
        expiresIn : ONE_WEEK
    })
}

export async function login(req, res) {
    try {
        const {email, password} = req.body
        const user = await User.findOne({
            where: {
                email: email
            }
        })

        if(!user){
            res.status(403).send({
                error: 'The login information was incorrect'
            })
        }

        const isPasswordValid = password == user.password
        if(!isPasswordValid){
            res.status(403).send({
                error: 'The login information was incorrect'
            })
        }

        const userJSON = user.toJSON()
        res.send({
            user : userJSON,
            token: jwtSignUser(userJSON)
        })
    } catch (err) {
        res.status(500).send({
            error: 'Error Occured Logging In.'
        });
    }
}

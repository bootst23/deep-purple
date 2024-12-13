/* eslint-disable @typescript-eslint/no-unused-vars */
/* eslint-disable @typescript-eslint/no-require-imports */
import { login } from "../controller/AuthenticationController.js";
const Joi = require('joi')

export default {
    register (req, res, next){
        const schema = {
            email: Joi.string().email(),
            password: Joi.string
        }

        const {error, value} = Joi.validate(req.body, schema)
        if(error){
            switch (error.details[0].context.key){
                case 'email':
                    break
                case 'password':
                    break
                default:
            }
        }else{
           next() 
        }
        
    },

    login (req, res, next) {
        
    }

    
}
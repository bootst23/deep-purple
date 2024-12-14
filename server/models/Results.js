//import { FLOAT } from "sequelize";

export default (sequelize, DataTypes) => {
    const Results = sequelize.define('Results', {
        name: {
            type: DataTypes.STRING
        },
        content: {
            type: DataTypes.TEXT,
        },
        input_type: {
            type: DataTypes.STRING,
        },
        anger_score: {
            type: DataTypes.FLOAT,
        },
        disgust_score: {
            type: DataTypes.FLOAT,
        },
        fear_score: {
            type: DataTypes.FLOAT,
        },
        joy_score: {
            type: DataTypes.FLOAT,
        },
        neutral_score: {
            type: DataTypes.FLOAT,
        },
        sadness_score: {
            type: DataTypes.FLOAT,
        },
        surprise_score: {
            type: DataTypes.FLOAT,
        }
    });
    return Results; // Return the defined model
};

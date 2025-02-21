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
        },
        dominant_emotion: {
            type: DataTypes.STRING,
        },
        summary: {
            type: DataTypes.TEXT,
        },
        actionable_insights: {
            type: DataTypes.TEXT,
        },
        suggested_response: {
            type: DataTypes.TEXT,
        },
    });
    return Results; // Return the defined model
};

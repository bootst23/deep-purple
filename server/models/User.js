export default (sequelize, DataTypes) => {
    const User = sequelize.define('User', {
        email: {
            type: DataTypes.STRING,
            unique: true,
        },
        password: {
            type: DataTypes.STRING,
        },
        userProfile: {
            type: DataTypes.STRING,
        },
    });
    return User; // Return the defined model
};

import axios from "axios";

export default () => {
    return axios.create({
        baseURL : `https://deep-purple-server.onrender.com` //Backend API
    })
}
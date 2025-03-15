import axios from "axios";

export default () => {
    return axios.create({
        baseURL : `https://deep-purple-server-gc60.onrender.com` //Backend API
    })
}
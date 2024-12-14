//Controllers are to decleare Endpoints

import {login} from './controller/AuthenticationController.js'
import {post, index, show} from './controller/ResultsController.js'

export default (app) => {
    app.post('/login', login)
    app.get('/results', index)
    app.post('/results', post)
    app.get('/results/:resultId', show)
}




// /services/ResultsService.js

import api from '@/services/api';

export default {
  // Fetch all results
  index() {
    return api().get('results');
  },
  
  // Fetch a single result by resultId
  show(resultId) {
    return api().get(`results/${resultId}`);
  }
};

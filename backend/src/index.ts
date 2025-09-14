import express from 'express';
import cors from 'cors';
import { search } from './recommendationEngine';
import { RecommendationRequest } from './types';

const app = express();
app.use(cors());
app.use(express.json());

app.post('/api/recommendations/search', (req, res) => {
  const body: RecommendationRequest = req.body;
  const data = search(body);
  res.json(data);
});

const PORT = process.env.PORT || 3001;
if (process.env.NODE_ENV !== 'test') {
  app.listen(PORT, () => {
    console.log(`Backend listening on port ${PORT}`);
  });
}

export default app;

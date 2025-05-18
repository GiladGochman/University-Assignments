import express from 'express';
import cors from 'cors';
import 'express-async-errors';
import noteRoutes from './routes/noteRoutes';
import { requestLogger } from './middlewares/logger';
import { errorHandler } from './middlewares/errorHandler';
import { Request, Response } from 'express';
import testRouter from './routes/testRouter';

const app = express();

app.use(cors());
app.use(express.json());
app.use(requestLogger);
app.use('/notes', noteRoutes); //connect all notes routes 
app.get('/health', (req: Request, res: Response) => res.send('OK')); //check server run 

if (process.env.NODE_ENV === 'dev') {
  app.use('/test', testRouter);
}

app.use(errorHandler);

export default app;
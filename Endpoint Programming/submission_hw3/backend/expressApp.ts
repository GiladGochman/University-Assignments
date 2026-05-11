import express from 'express';
import cors from 'cors';
import 'express-async-errors';
import noteRoutes from './routes/noteRoutes';
import { requestLogger } from './middlewares/logger';
import { errorHandler } from './middlewares/errorHandler';
import { Request, Response } from 'express';
import testRouter from './routes/testRouter';

import userRoutes from './routes/users';
import loginRoutes from './routes/login';

const app = express();

app.use(cors({ exposedHeaders: ['X-Total-Count'] }));
app.use(express.json());
app.use(requestLogger);

app.use('/users', userRoutes);
app.use('/login', loginRoutes);
app.use('/notes', noteRoutes);

if (process.env.NODE_ENV !== 'production') {
  app.use('/test', testRouter);
}
app.get('/health', (req: Request, res: Response) => res.send('OK')); //check server run 

app.use(errorHandler);

export default app;
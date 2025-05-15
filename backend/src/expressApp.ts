import express from 'express';
import cors from 'cors';
import 'express-async-errors';
import noteRoutes from './routes/noteRoutes';
import { requestLogger } from './middlewares/logger';
import { errorHandler } from './middlewares/errorHandler';
import { Request, Response } from 'express';

const app = express();

app.use(cors());
app.use(express.json());
app.use(requestLogger);
app.use('/notes', noteRoutes);
app.get('/health', (req: Request, res: Response) => res.send('OK'));

app.use(errorHandler);

export default app;
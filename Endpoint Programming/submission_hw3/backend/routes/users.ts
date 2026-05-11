import { Router } from 'express';
import { createUser } from '../controllers/users';
const router = Router();
router.post('/', createUser);
export default router;
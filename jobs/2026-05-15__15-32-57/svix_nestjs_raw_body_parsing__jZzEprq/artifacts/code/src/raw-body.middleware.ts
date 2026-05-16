import { Injectable, NestMiddleware } from '@nestjs/common';
import { Request, Response, NextFunction } from 'express';

declare module 'express' {
  interface Request {
    rawBody?: Buffer;
  }
}

@Injectable()
export class RawBodyMiddleware implements NestMiddleware {
  use(req: Request, res: Response, next: NextFunction) {
    // Only capture raw body for webhook endpoint
    if (req.path === '/webhook' && req.method === 'POST') {
      const chunks: Buffer[] = [];

      req.on('data', (chunk: Buffer) => {
        chunks.push(chunk);
      });

      req.on('end', () => {
        req.rawBody = Buffer.concat(chunks);
        next();
      });
    } else {
      next();
    }
  }
}

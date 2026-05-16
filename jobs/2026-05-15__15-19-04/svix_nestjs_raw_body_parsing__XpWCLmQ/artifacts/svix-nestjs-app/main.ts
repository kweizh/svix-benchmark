import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { json } from 'express';

async function bootstrap() {
  const app = await NestFactory.create(AppModule, { bodyParser: false });

  // Mount a JSON body parser that stores the raw body buffer on the request
  // object so that the /webhook route can access the original bytes for
  // cryptographic signature verification via the Svix SDK.
  app.use(
    json({
      verify: (req: any, _res, buf) => {
        req.rawBody = buf;
      },
    }),
  );

  await app.listen(process.env.PORT ?? 3000);
}
bootstrap();

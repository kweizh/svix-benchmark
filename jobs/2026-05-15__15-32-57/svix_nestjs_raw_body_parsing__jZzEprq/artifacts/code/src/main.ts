import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { RawBodyMiddleware } from './raw-body.middleware';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // Apply raw body middleware before body parsing
  app.use(new RawBodyMiddleware().use.bind(new RawBodyMiddleware()));

  await app.listen(process.env.PORT ?? 3000);
}
void bootstrap();

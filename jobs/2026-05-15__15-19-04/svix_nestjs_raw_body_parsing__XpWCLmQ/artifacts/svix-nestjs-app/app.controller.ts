import {
  BadRequestException,
  Controller,
  Get,
  HttpCode,
  Post,
  Req,
  Res,
} from '@nestjs/common';
import type { Request, Response } from 'express';
import { Webhook } from 'svix';
import { AppService } from './app.service';

const WEBHOOK_SECRET = 'whsec_MfKQ9r8GffUjCNNdXbn5O6vTmQxOQ9XQ';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get()
  getHello(): string {
    return this.appService.getHello();
  }

  @Post('webhook')
  @HttpCode(200)
  handleWebhook(
    @Req() req: Request & { rawBody?: Buffer },
    @Res() res: Response,
  ) {
    const rawBody = req.rawBody;

    if (!rawBody) {
      throw new BadRequestException('Missing raw body');
    }

    const svixId = req.headers['svix-id'] as string;
    const svixTimestamp = req.headers['svix-timestamp'] as string;
    const svixSignature = req.headers['svix-signature'] as string;

    if (!svixId || !svixTimestamp || !svixSignature) {
      throw new BadRequestException('Missing svix headers');
    }

    const wh = new Webhook(WEBHOOK_SECRET);

    try {
      wh.verify(rawBody, {
        'svix-id': svixId,
        'svix-timestamp': svixTimestamp,
        'svix-signature': svixSignature,
      });
    } catch {
      return res.status(400).json({ message: 'Invalid signature' });
    }

    return res.status(200).json({ message: 'Webhook received' });
  }
}

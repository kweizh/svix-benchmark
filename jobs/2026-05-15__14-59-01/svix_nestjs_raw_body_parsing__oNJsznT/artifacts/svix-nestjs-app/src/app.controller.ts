import { Controller, Get, Post, Req, Res } from '@nestjs/common';
import { Request, Response } from 'express';
import { Webhook } from 'svix';
import { AppService } from './app.service';

const SVIX_WEBHOOK_SECRET =
  'whsec_MfKQ9r8GffUjCNNdXbn5O6vTmQxOQ9XQ';

type RequestWithRawBody = Request & { rawBody?: Buffer };

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get()
  getHello(): string {
    return this.appService.getHello();
  }

  @Post('webhook')
  handleWebhook(@Req() req: RequestWithRawBody, @Res() res: Response) {
    const payload = req.rawBody?.toString('utf8');
    if (!payload) {
      return res.status(400).send('Missing raw body');
    }

    const headers = {
      'svix-id': req.header('svix-id') ?? '',
      'svix-timestamp': req.header('svix-timestamp') ?? '',
      'svix-signature': req.header('svix-signature') ?? '',
    };

    try {
      const webhook = new Webhook(SVIX_WEBHOOK_SECRET);
      webhook.verify(payload, headers);
      return res.status(200).send('OK');
    } catch (error) {
      return res.status(400).send('Invalid signature');
    }
  }
}

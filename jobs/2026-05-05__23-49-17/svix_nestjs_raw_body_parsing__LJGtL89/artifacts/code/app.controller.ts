import { Controller, Get, Post, Req, Res, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';
import * as express from 'express';
import { Webhook } from 'svix';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get()
  getHello(): string {
    return this.appService.getHello();
  }

  @Post('webhook')
  async handleWebhook(@Req() req: any, @Res() res: express.Response) {
    const payload = req.rawBody.toString('utf8');
    const headers = req.headers;
    const secret = 'whsec_MfKQ9r8GffUjCNNdXbn5O6vTmQxOQ9XQ';

    const wh = new Webhook(secret);

    try {
      wh.verify(payload, headers);
    } catch (err) {
      return res.status(HttpStatus.BAD_REQUEST).send({
        message: 'Invalid signature',
      });
    }

    return res.status(HttpStatus.OK).send({
      message: 'Webhook verified',
    });
  }
}

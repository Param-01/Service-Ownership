import { Body, Controller, Get, HttpCode, Param, Patch, Post, Query } from '@nestjs/common';
import { ServicesService } from './services.service';
import { CreateServiceDto } from './dto/create-service.dto';
import { UpdateServiceDto } from './dto/update-service.dto';

@Controller('services')
export class ServicesController {
  constructor(private readonly servicesService: ServicesService) {}

  @Get()
  findAll(@Query('team_id') teamId?: string) {
    return this.servicesService.findAll(teamId);
  }

  @Get('summary')
  getSummary(@Query('team_id') teamId?: string) {
    return this.servicesService.getSummary(teamId);
  }

  @Post()
  @HttpCode(201)
  create(@Body() dto: CreateServiceDto) {
    return this.servicesService.create(dto);
  }

  @Patch(':id')
  update(@Param('id') id: string, @Body() dto: UpdateServiceDto) {
    return this.servicesService.update(id, dto);
  }

  @Post(':id/deprecate')
  deprecate(@Param('id') id: string) {
    return this.servicesService.deprecate(id);
  }
}

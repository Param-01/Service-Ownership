import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { Service } from './entities/service.entity';
import { Team } from '../teams/entities/team.entity';
import { ServicesController } from './services.controller';
import { ServicesService } from './services.service';

@Module({
  imports: [TypeOrmModule.forFeature([Service, Team])],
  controllers: [ServicesController],
  providers: [ServicesService],
})
export class ServicesModule {}

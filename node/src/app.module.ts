import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { TeamsModule } from './teams/teams.module';
import { ServicesModule } from './services/services.module';
import { HealthModule } from './health/health.module';
import { Team } from './teams/entities/team.entity';
import { Service } from './services/entities/service.entity';

@Module({
  imports: [
    TypeOrmModule.forRoot({
      type: 'mysql',
      host: process.env.DB_HOST ?? 'localhost',
      port: Number(process.env.DB_PORT ?? 3306),
      username: process.env.DB_USER ?? 'root',
      password: process.env.DB_PASSWORD ?? 'password',
      database: process.env.DB_NAME ?? 'service_ownership_node',
      entities: [Team, Service],
      synchronize: true,
    }),
    HealthModule,
    TeamsModule,
    ServicesModule,
  ],
})
export class AppModule {}

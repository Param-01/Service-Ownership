import {
  BadRequestException,
  ConflictException,
  Injectable,
  NotFoundException,
} from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Service, ServiceStatus } from './entities/service.entity';
import { Team } from '../teams/entities/team.entity';
import { CreateServiceDto } from './dto/create-service.dto';
import { UpdateServiceDto } from './dto/update-service.dto';

@Injectable()
export class ServicesService {
  constructor(
    @InjectRepository(Service)
    private readonly serviceRepo: Repository<Service>,
    @InjectRepository(Team)
    private readonly teamRepo: Repository<Team>,
  ) {}

  async findAll(teamId?: string): Promise<Service[]> {
    const qb = this.serviceRepo
      .createQueryBuilder('s')
      .leftJoinAndSelect('s.team', 'team');
    if (teamId) qb.where('s.teamId = :teamId', { teamId });
    return qb.getMany();
  }

  async getSummary(teamId?: string) {
    const countQb = this.serviceRepo
      .createQueryBuilder('s')
      .select('s.status', 'status')
      .addSelect('COUNT(*)', 'count');
    if (teamId) countQb.where('s.teamId = :teamId', { teamId });
    const rows: { status: string; count: string }[] = await countQb
      .groupBy('s.status')
      .getRawMany();

    const countMap = Object.fromEntries(rows.map((r) => [r.status, Number(r.count)]));
    const totalActive = countMap[ServiceStatus.ACTIVE] ?? 0;
    const totalDeprecated = countMap[ServiceStatus.DEPRECATED] ?? 0;

    if (teamId) {
      const team = await this.teamRepo.findOne({ where: { id: teamId }, relations: ['service'] });
      if (!team) throw new NotFoundException('Team not found');
      return {
        total_services: totalActive + totalDeprecated,
        total_active: totalActive,
        total_deprecated: totalDeprecated,
        total_teams: 1,
        teams: [{ team_id: team.id, team_name: team.name, service: team.service ?? null }],
      };
    }

    const allTeams = await this.teamRepo.find({ relations: ['service'] });
    return {
      total_services: totalActive + totalDeprecated,
      total_active: totalActive,
      total_deprecated: totalDeprecated,
      total_teams: allTeams.length,
      teams: allTeams.map((t) => ({ team_id: t.id, team_name: t.name, service: t.service ?? null })),
    };
  }

  async create(dto: CreateServiceDto): Promise<Service> {
    const team = await this.teamRepo.findOne({
      where: { id: dto.teamId },
      relations: ['service'],
    });
    if (!team) throw new NotFoundException('Team not found');
    if (team.service) throw new ConflictException('Team already owns a service');

    const existing = await this.serviceRepo.findOneBy({ name: dto.name });
    if (existing) throw new ConflictException('Service name already exists');

    const service = this.serviceRepo.create({
      name: dto.name,
      description: dto.description ?? null,
      teamId: dto.teamId,
    });
    const saved = await this.serviceRepo.save(service);
    return this.serviceRepo.findOne({ where: { id: saved.id }, relations: ['team'] }) as Promise<Service>;
  }

  async update(id: string, dto: UpdateServiceDto): Promise<Service> {
    const service = await this.serviceRepo.findOne({ where: { id }, relations: ['team'] });
    if (!service) throw new NotFoundException('Service not found');

    if (dto.name !== undefined) service.name = dto.name;
    if ('description' in dto) service.description = dto.description ?? null;

    if ('teamId' in dto) {
      const newTeamId = dto.teamId ?? null;
      if (newTeamId !== null) {
        const newTeam = await this.teamRepo.findOne({
          where: { id: newTeamId },
          relations: ['service'],
        });
        if (!newTeam) throw new NotFoundException('Team not found');
        if (newTeam.service && newTeam.service.id !== id)
          throw new ConflictException('Team already owns a service');
      }
      service.teamId = newTeamId;
    }

    const existing = await this.serviceRepo.findOneBy({ name: service.name });
    if (existing && existing.id !== id) throw new ConflictException('Service name already exists');

    await this.serviceRepo.save(service);
    return this.serviceRepo.findOne({ where: { id }, relations: ['team'] }) as Promise<Service>;
  }

  async deprecate(id: string): Promise<Service> {
    const service = await this.serviceRepo.findOne({ where: { id }, relations: ['team'] });
    if (!service) throw new NotFoundException('Service not found');
    if (service.status === ServiceStatus.DEPRECATED)
      throw new BadRequestException('Service is already deprecated');

    service.status = ServiceStatus.DEPRECATED;
    service.deprecatedAt = new Date();
    service.teamId = null;
    await this.serviceRepo.save(service);
    return this.serviceRepo.findOne({ where: { id }, relations: ['team'] }) as Promise<Service>;
  }
}

import { IsNotEmpty, IsOptional, IsString } from 'class-validator';

export class CreateTeamDto {
  @IsString()
  @IsNotEmpty({ message: 'name cannot be empty' })
  name: string;

  @IsOptional()
  @IsString()
  description?: string | null;
}

import { IsNotEmpty, IsOptional, IsString, IsUUID } from 'class-validator';

export class CreateServiceDto {
  @IsString()
  @IsNotEmpty({ message: 'name cannot be empty' })
  name: string;

  @IsUUID()
  teamId: string;

  @IsOptional()
  @IsString()
  description?: string | null;
}

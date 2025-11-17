export interface TestResult {
  success: boolean;
  latency: number;
  sample?: string;
  error?: string;
}

export interface ValidationResult {
  valid: boolean;
  errors: string[];
}

export interface ProviderSettings {
  [key: string]: any;
}

export abstract class ProviderAdapter {
  abstract testConnection(settings: ProviderSettings): Promise<TestResult>;
  abstract validateSettings(settings: ProviderSettings): Promise<ValidationResult>;

  protected maskSensitiveData(data: string): string {
    if (data.length <= 10) {
      return '***';
    }
    return data.substring(0, 5) + '***' + data.substring(data.length - 5);
  }
}

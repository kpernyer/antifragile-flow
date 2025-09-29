export interface FileMetadata {
  file: File;
  status: 'scanning' | 'completed';
  metadata?: {
    summary: string;
    format: string;
    title: string;
    length: number;
    topic: string;
    sentiment: string;
  };
}

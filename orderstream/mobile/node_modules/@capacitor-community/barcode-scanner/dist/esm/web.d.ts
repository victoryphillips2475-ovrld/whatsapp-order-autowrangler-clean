import { WebPlugin } from '@capacitor/core';
import type { BarcodeScannerPlugin, ScanOptions, ScanResult, CheckPermissionOptions, CheckPermissionResult, StopScanOptions, TorchStateResult } from './definitions';
export declare class BarcodeScannerWeb extends WebPlugin implements BarcodeScannerPlugin {
    prepare(): Promise<void>;
    hideBackground(): Promise<void>;
    showBackground(): Promise<void>;
    startScan(_options: ScanOptions): Promise<ScanResult>;
    startScanning(_options: ScanOptions, _callback: any): Promise<string>;
    pauseScanning(): Promise<void>;
    resumeScanning(): Promise<void>;
    stopScan(_options?: StopScanOptions): Promise<void>;
    checkPermission(_options: CheckPermissionOptions): Promise<CheckPermissionResult>;
    openAppSettings(): Promise<void>;
    disableTorch(): Promise<void>;
    enableTorch(): Promise<void>;
    toggleTorch(): Promise<void>;
    getTorchState(): Promise<TorchStateResult>;
}

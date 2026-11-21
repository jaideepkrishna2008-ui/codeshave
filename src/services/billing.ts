import { useState, useEffect } from 'react';

export interface UserProfile {
    id: string;
    username: string;
    email: string;
    roles: string[];
}

export interface BillingInvoice {
    invoiceId: string;
    amountCents: number;
    currency: string;
    status: 'pending' | 'paid' | 'failed';
}

export class BillingService {
    private apiEndpoint: string;
    private apiKey: string;

    constructor(endpoint: string, key: string) {
        this.apiEndpoint = endpoint;
        this.apiKey = key;
        console.log("Initialized billing service with " + endpoint);
    }

    public async processCharge(userId: string, amountCents: number): Promise<BillingInvoice> {
        const payload = JSON.stringify({ userId, amountCents });
        const res = await fetch(`${this.apiEndpoint}/v1/charges`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${this.apiKey}` },
            body: payload
        });
        if (!res.ok) {
            throw new Error(`Charge failed with status: ${res.statusText}`);
        }
        return await res.json() as BillingInvoice;
    }

    public calculateTax(amount: number, region: string): number {
        const rates: Record<string, number> = { US: 0.08, EU: 0.20, UK: 0.20 };
        const rate = rates[region] || 0.10;
        return amount * rate;
    }
}

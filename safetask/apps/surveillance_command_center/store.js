import { create } from 'zustand';

const useStore = create((set) => ({
  activeTab: 'dashboard',
  agentRole: 'surveillance',
  protectedCameras: [],
  activeIncidents: [],
  setActiveTab: (tab) => set({ activeTab: tab }),
  setAgentRole: (role) => set({ agentRole: role }),
  addProtectedCamera: (camera) => set((state) => ({ protectedCameras: [...state.protectedCameras, camera] })),
  removeProtectedCamera: (camera) => set((state) => ({ protectedCameras: state.protectedCameras.filter(c => c !== camera) })),
  addActiveIncident: (incident) => set((state) => ({ activeIncidents: [...state.activeIncidents, incident] })),
  removeActiveIncident: (incident) => set((state) => ({ activeIncidents: state.activeIncidents.filter(i => i !== incident) }))
}));

export default useStore;
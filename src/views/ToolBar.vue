<template>
  <div class="flex">
    <!-- Hamburger Menu (Moves with Sidebar) -->
    <div
      :class="[
        'fixed top-4 z-50 p-3 cursor-pointer flex justify-center items-center transition-all duration-300',
        sidebarOpen ? 'left-64' : 'left-4',
      ]"
      @click="toggleSidebar"
    >
      <div class="space-y-1">
        <div class="w-6 h-0.5 bg-gray-400"></div>
        <div class="w-6 h-0.5 bg-gray-400"></div>
        <div class="w-6 h-0.5 bg-gray-400"></div>
      </div>
    </div>

    <!-- Sidebar -->
    <div
      :class="[
        'fixed z-50 top-0 left-0 h-full bg-[#1f2937] text-white shadow-lg transition-all duration-300 flex flex-col',
        sidebarOpen ? 'w-64' : 'w-0', // Hide sidebar completely when closed
      ]"
    >
      <!-- Search Bar -->
      <div v-if="sidebarOpen" class="p-4 border-b border-gray-600">
        <input
          type="text"
          class="w-full bg-gray-200 text-black p-2 rounded-lg placeholder-gray-600"
          placeholder="Search..."
          v-model="searchQuery"
        />
      </div>

      <!-- Navigation Links -->
      <div v-if="sidebarOpen" class="p-4">
        <h3 class="text-lg font-semibold border-b border-gray-600 pb-2">
          Deep Purple
        </h3>
        <div class="mt-3 space-y-3">
          <router-link
            to="/"
            class="block text-sm font-medium hover:text-[#9ca3af] transition"
          >
            Home
          </router-link>
          <router-link
            to="/fileUpload"
            class="block text-sm font-medium hover:text-[#9ca3af] transition"
          >
            Detect Emotions
          </router-link>

          <router-link
            to="/history"
            class="block text-sm font-medium hover:text-[#9ca3af] transition"
          >
            History
          </router-link>
        </div>
      </div>

      <!-- Sign In at the Bottom -->
      <div v-if="sidebarOpen" class="p-4 border-t border-gray-600">
        <router-link
          to="/login"
          class="block text-lg font-medium hover:text-[#9ca3af] transition"
        >
          Sign In
        </router-link>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
export default {
  name: "SideBar",
  data() {
    return {
      sidebarOpen: true,
      searchQuery: "",
      entries: [
        { id: 1, title: "Customer Complaint 1" },
        { id: 2, title: "Customer Complaint 2" },
        { id: 3, title: "Customer Complaint 3" },
        { id: 4, title: "Customer Complaint 4" },
      ],
    };
  },
  computed: {
    filteredEntries() {
      if (!this.searchQuery) return this.entries;
      return this.entries.filter((entry) =>
        entry.title.toLowerCase().includes(this.searchQuery.toLowerCase())
      );
    },
  },
  methods: {
    toggleSidebar() {
      this.sidebarOpen = !this.sidebarOpen;
    },
    viewEntry(id: number) {
      console.log(`Viewing entry ${id}`);
    },
  },
};
</script>

<style scoped>
/* All scoped styles replaced by Tailwind classes */
</style>

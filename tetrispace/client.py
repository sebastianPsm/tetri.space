import os, sys
import functools
import random
import threading
import pygame
import pygame_gui

import grpc
import tetrispace_pb2
import tetrispace_pb2_grpc

class Field:
    def __init__(self, surface, pos, size, factor, bg_color='#FFFFFF'):
        assert type(pos)==tuple, "Type of pos-parameter must be tuple"
        assert type(size)==tuple, "Type of size-parameter must be tuple"
        assert len(pos)==2, "Length of pos-parameter must be 2"
        assert len(size)==2, "Length of size-parameter must be 2"

        self.surface = surface
        self.pos = pos
        self.size = size
        self.bg_color = bg_color
        self.factor = factor

        self.field_bg = pygame.Surface((size[0]*factor,size[1]*factor))
        self.field_bg.fill(pygame.Color(self.bg_color))
    
    def set_data(self, data=None):
        self.field_bg.fill(pygame.Color(self.bg_color))
        if not data:
            data = []
            for idx in range(self.size[0] * self.size[1]):
                data.append(random.randrange(2))
        
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                color = (0,0,0) if data[y * self.size[0] + x] else (255,255,255)
                rect = pygame.Rect(x*self.factor, y*self.factor, self.factor, self.factor)
                pygame.draw.rect(self.field_bg, color, rect)

    def blit(self):
        self.surface.blit(self.field_bg, self.pos)

class FieldStatusThread(threading.Thread):
    def __init__(self, field_status_stream, client):
        threading.Thread.__init__(self)
        self.field_status_stream = field_status_stream
        self.loop = True
        self.client = client
    
    def stop(self):
        self.loop = False
    
    def run(self):
        while self.loop:
            field_status = next(self.field_status_stream)
            self.client.set_field_status(field_status)

class TetriSpaceClient:
    def __init__(self, factor):
        # UI
        window_size = 25*factor, 16*factor 
        pygame.init()
        pygame.display.set_caption("tetri.space test client")
        self.window_surface = pygame.display.set_mode(window_size)

        self.background = pygame.Surface(window_size)
        self.background.fill(pygame.Color('#000000'))
        
        self.manager = pygame_gui.UIManager(window_size, os.path.join(os.path.dirname(__file__), 'data/theme.json'))
        self.clock = pygame.time.Clock()

        self.draw_gui(self.manager, factor)

        self.main_field = Field(self.window_surface, (factor, factor), (12,24), 20)
        self.fields = [Field(self.window_surface, (13*factor + (pos%3)*130, factor + (pos%2) * 250), (12,24), 9) for pos in range(6)]

        # Connection via grpc
        self.channel = None
        self.stub = None
        self.instance = None
        self.field_key = None
        self.field_status_stream = None

        # Game logic
        self.is_running = True
    
    def connected(self, future_context, create):
        self.create_button.disable()

        if create:
            self.instance = self.stub.CreateInstance(tetrispace_pb2.InstanceParameter(fields=6,height=24,width=12))
            self.random_word_entry.set_text(self.instance.random_word)
        
        self.field_key = self.stub.GetField(tetrispace_pb2.InstanceIdentifier(random_word=self.random_word_entry.get_text()))
        self.field_status_stream = self.stub.GetFieldStatusStream(self.field_key)
        self.field_status_thread = FieldStatusThread(self.field_status_stream, self)
        self.field_status_thread.start()
        self.join_button.set_text("Set ready")

    def connect_server(self, server_host, create=False):
        self.channel = grpc.insecure_channel(server_host)
        self.stub = tetrispace_pb2_grpc.TetrispaceStub(self.channel)

        future = grpc.channel_ready_future(self.channel)
        future.add_done_callback(lambda future_context: self.connected(future_context, create))
    
    def set_ready(self):
        self.stub.SetReady(self.field_key)
        self.join_button.disable()

    def disconnect_game(self):
        if self.instance:
            self.stub.DeleteInstance(self.instance)

        if self.channel:
            self.channel.close()
        
    def set_field_status(self, field_status):
        print(f"field_status.max_fields: {field_status.max_fields}, field_status.fields: {field_status.fields}, field_status.set_ready_fields: {field_status.set_ready_fields}")

        if(self.stub):
            pass
            #field = self.stub.GetField(tetrispace_pb2.FieldKey(uuid=self.myField))
            #self.main_field.set_data(field.data)

            #field_size = field.height * field.width
            #for idx, field_ui in enumerate(self.fields):
            #    field_ui.set_data(field.others[idx*field_size:idx*field_size+field_size])
        

    def blit(self):
        for field in self.fields:
            field.blit()
        self.main_field.blit()
    
    def draw_gui(self, manager, factor):
        random_word_pos    = (8*factor,   0*factor+2), (6*factor,   1*factor)
        me_pos       = (1*factor,   1*factor),   (6*factor,  12*factor)
        next_pos     = (8*factor,   1*factor),   (4*factor,   4*factor)
        specials_pos = (8*factor,   4*factor),   (1*factor,  18*factor)
        join_pos     = (4*factor,   0*factor),   (4*factor,   1*factor)
        create_pos   = (0*factor,   0*factor),   (4*factor,   1*factor)
        f_pos        = (23*factor,  0*factor),   (1*factor,   1*factor)
        x_pos        = (24*factor,  0*factor),   (1*factor,   1*factor)
        #number_1_pos = (12*factor,  1*factor),   (4*factor,   8*factor)
        #number_2_pos = (15*factor,  1*factor),   (4*factor,   8*factor)
        #number_3_pos = (20*factor,  1*factor),   (4*factor,   8*factor)
        #number_4_pos = (12*factor,  6*factor),   (4*factor,   8*factor)
        #number_5_pos = (15*factor,  6*factor),   (4*factor,   8*factor)
        #number_6_pos = (20*factor,  6*factor),   (4*factor,   8*factor)

        self.join_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(join_pos[0], join_pos[1]), text='Join', manager=manager)
        self.create_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(create_pos[0], create_pos[1]), text='Create', manager=manager)
        self.fullscreen_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(f_pos[0], f_pos[1]), text='F', manager=manager)
        self.exit_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(x_pos[0], x_pos[1]), text='X', manager=manager)
        self.random_word_entry = pygame_gui.elements.ui_text_entry_line.UITextEntryLine(relative_rect=pygame.Rect(random_word_pos[0], random_word_pos[1]), manager=manager)
        
    def start(self):
        while self.is_running:
            self.loop()
            pygame.display.flip()
        
        if self.field_status_stream:
            self.field_status_thread.stop()
            self.field_status_thread.join()
        self.disconnect_game()

    def quit(self):
        self.is_running = False
    
    def toggle_fullscreen(self):
        print("Toggle fullscreen")
        if self.fullscreen_button.text == "F":
            pygame.display.set_mode(flags=pygame.FULLSCREEN)
            self.fullscreen_button.set_text("W")
        else:
            pygame.display.set_mode(flags=pygame.RESIZABLE)
            self.fullscreen_button.set_text("F")

    def loop(self):
        time_delta = self.clock.tick(60)/1000.0

        # Event loop
        for event in pygame.event.get():
            # Quit
            if event.type == pygame.QUIT:
                self.quit()
            if event.type == pygame.USEREVENT:
                if event.ui_element == self.fullscreen_button:
                    self.toggle_fullscreen()
                if event.ui_element == self.exit_button:
                    self.quit()
                if event.ui_element == self.join_button:
                    if self.join_button.text == "Join":
                        self.connect_server("localhost:5000", create=False)
                    else:
                        self.set_ready()
                if event.ui_element == self.create_button:
                    self.connect_server("localhost:5000", create=True)
            self.manager.process_events(event)
        self.manager.update(time_delta)
        self.manager.draw_ui(self.window_surface)
        self.blit()
        pygame.display.update()

if __name__ == "__main__":
    tsc = TetriSpaceClient(34)
    tsc.start()
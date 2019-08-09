import torch
import evaluate

import os
import numpy as np
import shutil
import collections

def save_hyperparameters(hyperparameters, folder) :
    """
        Save the hyperparameters in the file Hyperparameters.txt
        in the folder folder
    """
    if not os.path.exists(folder) :
        os.makedirs(folder)
        
    if type(hyperparameters) == collections.OrderedDict:
        with open(folder + '/Hyperparameters.txt', 'w') as fichier :
            for ii, (key, value) in enumerate(list(hyperparameters.items())):
                if ii != 0 :
                    fichier.write('\n')
                fichier.write(str(key) + ' = ' + str(value))
    elif type(hyperparameters == list):
        with open(folder + '/Hyperparameters.txt', 'w') as fichier :
            key = ['batch_size', 'num_workers', 'conv_dim', 'z_size', 'lr', 'beta1', 'beta2', 'gradient penalty', 'epsilon', 'epochs', 'c_iter', 'latent_size'] 
            for ii, value in enumerate(hyperparameters):
                if ii != 0 :
                    fichier.write('\n')
                fichier.write(str(key[ii]) + ' = ' + str(value))


def save_model_IS_FID(IS_max, FID_min, real_images, fake_images, Classifier, Critic, Generator, checkpoint_path):
    """
        Compute IS and FID
        Verify is IS or FID is better
        Save the critic and the genrator if it's the case in the foler checkpoint_path
    """
    affichage = False
    score_IS = evaluate.inception_score(fake_images,Classifier)
    score_FID = evaluate.fid(real_images, fake_images, Classifier)

    if  score_IS > IS_max:
        IS_max = score_IS
        torch.save(Critic.state_dict(),checkpoint_path + 'Critic_IS.pth')
        torch.save(Generator.state_dict(),checkpoint_path + 'Generator_IS.pth')
        affichage = True

    if  score_FID < FID_min:
        FID_min = score_FID
        torch.save(Critic.state_dict(),checkpoint_path + 'Critic_FID.pth')
        torch.save(Generator.state_dict(),checkpoint_path + 'Generator_FID.pth')
        affichage = True 

    return score_IS, score_FID, IS_max, FID_min, affichage

def save_model_FID(FID_min, real_images, fake_images, Classifier, Critic, Generator, checkpoint_path):
    """
        Compute IS and FID
        Verify is IS or FID is better
        Save the critic and the genrator if it's the case in the foler checkpoint_path
    """
    affichage = False
    score_FID = evaluate.fid(real_images, fake_images, Classifier)

    if  score_FID < FID_min:
        FID_min = score_FID
        torch.save(Critic.state_dict(),checkpoint_path + 'Critic_FID.pth')
        torch.save(Generator.state_dict(),checkpoint_path + 'Generator_FID.pth')
        affichage = True 

    return score_FID, FID_min, affichage

def save_model(test_loss, test_loss_min, classifier, checkpoint_path, train_on_gpu):

    affichage = False

    if test_loss < test_loss_min:
        test_loss_min = test_loss.item()
        if train_on_gpu:
            classifier.cpu()
        torch.save(classifier.state_dict(), checkpoint_path + 'classifier.pth')
        if train_on_gpu:
            classifier.cuda()
        affichage = True
    return test_loss_min, affichage


def save_log(epoch, time, c_loss, g_loss, IS, FID, folder) :
    """
        Save epoch, time, c_loss, g_loss, IS, FID ine the log files log.csv
        in the folder folder
    """
    if not os.path.exists(folder + '/log.csv'):
        with open(folder+'/log.csv', 'w') as fichier :
            fichier.write('epoch ;time ;c_loss ;g_loss ;IS ;FID \n')
            fichier.write('{};{};{};{};{};{}\n'.format(epoch, time, c_loss, g_loss, IS, FID))
    else:
        with open(folder+'/log.csv', 'a') as fichier :
            fichier.write('{};{};{};{};{};{}\n'.format(epoch, time, c_loss, g_loss, IS, FID))


def save_log_AE(epoch, time, train_loss, test_loss, FID, folder) :
    """
        Save epoch, time, train_loss, test_loss, IS, FID ine the log files log.csv
        in the folder folder
    """
    if not os.path.exists(folder + '/log.csv'):
        with open(folder+'/log.csv', 'w') as fichier :
            fichier.write('epoch;time;train_loss;test_loss;FID\n')
            fichier.write('{};{};{};{};{}\n'.format(epoch, time, train_loss, test_loss, FID))
    else:
        with open(folder+'/log.csv', 'a') as fichier :
            fichier.write('{};{};{};{};{}\n'.format(epoch, time, train_loss, test_loss, FID))

def save_log_classifier(epoch, time, train_loss, test_loss, accuracy, folder) :
    """
        Save epoch, time, train_loss, test_loss, accuracy ine the log files log.csv
        in the folder folder
    """
    if not os.path.exists(folder + '/log.csv'):
        with open(folder+'/log.csv', 'w') as fichier :
            fichier.write('epoch;time;train_loss;test_loss;accuracy\n')
            fichier.write('{};{};{};{};{}\n'.format(epoch, time, train_loss, test_loss, accuracy))
    else:
        with open(folder+'/log.csv', 'a') as fichier :
            fichier.write('{};{};{};{};{}\n'.format(epoch, time, train_loss, test_loss, accuracy))


def save_best(IS_max, FID_min, hyperparameters, folder_src, folder_fin = '.'):
    # folder_src where find Best critic and generator in IS and FID during the training
    """
        Save the critic, the generator and the hyperparameters
        if the IS or the FID is better than all the training made yet
    """
    folder_IS = folder_fin + '/Best_IS/'
    folder_FID = folder_fin + '/Best_FID/'

    if not os.path.exists(folder_IS):
        os.makedirs(folder_IS)
        best_IS = 0
    else:
        with open(folder_IS + 'IS.txt', 'r') as fichier:
            best_IS = float(fichier.read())

    if not os.path.exists(folder_FID):
        os.makedirs(folder_FID)
        best_FID = np.inf
    else:        
        with open(folder_FID + 'FID.txt', 'r') as fichier:
            best_FID = float(fichier.read())

    if best_IS < IS_max:
        save_hyperparameters(hyperparameters, folder_IS)
        shutil.copyfile(folder_src + '/Critic_IS.pth', folder_IS + 'Critic_IS.pth')
        shutil.copyfile(folder_src + '/Generator_IS.pth', folder_IS + 'Generator_IS.pth')
        shutil.copyfile(folder_src + '/../log.csv', folder_IS + 'log.csv')
        with open(folder_IS + 'IS.txt', 'w') as fichier:
            fichier.write(str(IS_max))

    if FID_min < best_FID:
        save_hyperparameters(hyperparameters, folder_FID)
        shutil.copyfile(folder_src + '/Critic_FID.pth',folder_FID + 'Critic_FID.pth')
        shutil.copyfile(folder_src + '/Generator_FID.pth',folder_FID + 'Generator_FID.pth')
        shutil.copyfile(folder_src + '/../log.csv', folder_FID + 'log.csv')
        with open(folder_FID + 'FID.txt', 'w') as fichier:
            fichier.write(str(FID_min))

def save_best_AE(FID_min, hyperparameters, Encoder, Decoder, vanilla):
    """
        Save the Encoder, the Decoder and the hyperparameters
        if the IS or the FID is better than all the training made yet
    """
    
    folder_FID = 'Best_AE_FID/'
    
    if not os.path.exists(folder_FID):
        os.makedirs(folder_FID)
        best_FID = np.inf
    else:
        with open(folder_FID + 'FID.txt', 'r') as fichier:
            best_FID = float(fichier.read())

    if FID_min < best_FID:
        save_hyperparameters(hyperparameters, folder_FID)
        torch.save(Encoder.state_dict(),folder_FID + 'Encoder_FID.pth')
        torch.save(Decoder.state_dict(),folder_FID + 'Decoder_FID.pth')
        with open(folder_FID + 'FID.txt', 'w') as fichier:
            fichier.write(str(FID_min))
    
        # Save also Encoder and decoder in ../checkpoints/Best_AE_FID/
        folder_FID = '../../checkpoints/AE_' + vanilla + '/Best_AE_FID/'

        if not os.path.exists(folder_FID):
            os.makedirs(folder_FID)

        save_hyperparameters(hyperparameters, folder_FID)
        torch.save(Encoder.state_dict(),folder_FID + 'Encoder_FID.pth')
        torch.save(Decoder.state_dict(),folder_FID + 'Decoder_FID.pth')
        with open(folder_FID + 'FID.txt', 'w') as fichier:
            fichier.write(str(FID_min))

def save_best_classifier(test_loss, hyperparameters, folder_src, folder_test_loss='../checkpoints/'):
    """
        Save the classifier and the hyperparameters
        if the test_loss is better than all the training made yet
    """
    
    if not os.path.exists(folder_test_loss):
        os.makedirs(folder_test_loss)
        best_test_loss = np.inf
    else:
        with open(folder_test_loss + 'Best_test_loss/test_loss.txt', 'r') as fichier:
            best_test_loss = float(fichier.read())

    if best_test_loss > test_loss:
        save_hyperparameters(hyperparameters, folder_test_loss + 'Best_test_loss')
        shutil.copyfile(folder_src + '/classifier.pth', folder_test_loss + 'classifier.pth')
        shutil.copyfile(folder_src + '/classifier.pth', folder_test_loss + 'Best_test_loss/classifier.pth')
        shutil.copyfile(folder_src + '/../log.csv', folder_test_loss + 'Best_test_loss/log.csv')
        with open(folder_test_loss + 'Best_test_loss/test_loss.txt', 'w') as fichier:
            fichier.write(str(test_loss))


def save_tested_hyperparameters(hyperparameters):
    """
        Save the hyperparameter of the training int the file hyperparameters.csv
    """
    with open('Tested_hyperparameters.csv', 'a') as fichier :
        for i, parameter in enumerate(list(hyperparameters.values())):
            if i != 0:
                fichier.write(';')
            fichier.write('{}'.format(str(parameter)))
        fichier.write('\n')